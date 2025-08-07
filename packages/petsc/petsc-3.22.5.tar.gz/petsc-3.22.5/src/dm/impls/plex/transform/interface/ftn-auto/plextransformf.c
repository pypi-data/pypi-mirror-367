#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* plextransform.c */
/* Fortran interface file */

/*
* This file was generated automatically by bfort from the C source
* file.  
 */

#ifdef PETSC_USE_POINTER_CONVERSION
#if defined(__cplusplus)
extern "C" { 
#endif 
extern void *PetscToPointer(void*);
extern int PetscFromPointer(void *);
extern void PetscRmPointer(void*);
#if defined(__cplusplus)
} 
#endif 

#else

#define PetscToPointer(a) (a ? *(PetscFortranAddr *)(a) : 0)
#define PetscFromPointer(a) (PetscFortranAddr)(a)
#define PetscRmPointer(a)
#endif

#include "petscdmplextransform.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplextransformcreate_ DMPLEXTRANSFORMCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplextransformcreate_ dmplextransformcreate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplextransformsettype_ DMPLEXTRANSFORMSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplextransformsettype_ dmplextransformsettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplextransformgettype_ DMPLEXTRANSFORMGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplextransformgettype_ dmplextransformgettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplextransformview_ DMPLEXTRANSFORMVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplextransformview_ dmplextransformview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplextransformsetfromoptions_ DMPLEXTRANSFORMSETFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplextransformsetfromoptions_ dmplextransformsetfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplextransformdestroy_ DMPLEXTRANSFORMDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplextransformdestroy_ dmplextransformdestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplextransformsetup_ DMPLEXTRANSFORMSETUP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplextransformsetup_ dmplextransformsetup
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplextransformgetdm_ DMPLEXTRANSFORMGETDM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplextransformgetdm_ dmplextransformgetdm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplextransformsetdm_ DMPLEXTRANSFORMSETDM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplextransformsetdm_ dmplextransformsetdm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplextransformgetactive_ DMPLEXTRANSFORMGETACTIVE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplextransformgetactive_ dmplextransformgetactive
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplextransformsetactive_ DMPLEXTRANSFORMSETACTIVE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplextransformsetactive_ dmplextransformsetactive
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplextransformsetdimensions_ DMPLEXTRANSFORMSETDIMENSIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplextransformsetdimensions_ dmplextransformsetdimensions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplextransformgettargetpoint_ DMPLEXTRANSFORMGETTARGETPOINT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplextransformgettargetpoint_ dmplextransformgettargetpoint
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplextransformgetsourcepoint_ DMPLEXTRANSFORMGETSOURCEPOINT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplextransformgetsourcepoint_ dmplextransformgetsourcepoint
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplextransformcelltransform_ DMPLEXTRANSFORMCELLTRANSFORM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplextransformcelltransform_ dmplextransformcelltransform
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplextransformgetsubcellorientation_ DMPLEXTRANSFORMGETSUBCELLORIENTATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplextransformgetsubcellorientation_ dmplextransformgetsubcellorientation
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplextransformmapcoordinates_ DMPLEXTRANSFORMMAPCOORDINATES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplextransformmapcoordinates_ dmplextransformmapcoordinates
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplextransformapply_ DMPLEXTRANSFORMAPPLY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplextransformapply_ dmplextransformapply
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmplextransformcreate_(MPI_Fint * comm,DMPlexTransform *tr, int *ierr)
{
PETSC_FORTRAN_OBJECT_CREATE(tr);
 PetscBool tr_null = !*(void**) tr ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(tr);
*ierr = DMPlexTransformCreate(
	MPI_Comm_f2c(*(comm)),tr);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! tr_null && !*(void**) tr) * (void **) tr = (void *)-2;
}
PETSC_EXTERN void  dmplextransformsettype_(DMPlexTransform tr,char *method, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(tr);
/* insert Fortran-to-C conversion for method */
  FIXCHAR(method,cl0,_cltmp0);
*ierr = DMPlexTransformSetType(
	(DMPlexTransform)PetscToPointer((tr) ),_cltmp0);
  FREECHAR(method,_cltmp0);
}
PETSC_EXTERN void  dmplextransformgettype_(DMPlexTransform tr,char *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(tr);
*ierr = DMPlexTransformGetType(
	(DMPlexTransform)PetscToPointer((tr) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for type */
*ierr = PetscStrncpy(type, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, type, cl0);
}
PETSC_EXTERN void  dmplextransformview_(DMPlexTransform tr,PetscViewer v, int *ierr)
{
CHKFORTRANNULLOBJECT(tr);
CHKFORTRANNULLOBJECT(v);
*ierr = DMPlexTransformView(
	(DMPlexTransform)PetscToPointer((tr) ),PetscPatchDefaultViewers((PetscViewer*)v));
}
PETSC_EXTERN void  dmplextransformsetfromoptions_(DMPlexTransform tr, int *ierr)
{
CHKFORTRANNULLOBJECT(tr);
*ierr = DMPlexTransformSetFromOptions(
	(DMPlexTransform)PetscToPointer((tr) ));
}
PETSC_EXTERN void  dmplextransformdestroy_(DMPlexTransform *tr, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(tr);
 PetscBool tr_null = !*(void**) tr ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(tr);
*ierr = DMPlexTransformDestroy(tr);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! tr_null && !*(void**) tr) * (void **) tr = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(tr);
 }
PETSC_EXTERN void  dmplextransformsetup_(DMPlexTransform tr, int *ierr)
{
CHKFORTRANNULLOBJECT(tr);
*ierr = DMPlexTransformSetUp(
	(DMPlexTransform)PetscToPointer((tr) ));
}
PETSC_EXTERN void  dmplextransformgetdm_(DMPlexTransform tr,DM *dm, int *ierr)
{
CHKFORTRANNULLOBJECT(tr);
PetscBool dm_null = !*(void**) dm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexTransformGetDM(
	(DMPlexTransform)PetscToPointer((tr) ),dm);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dm_null && !*(void**) dm) * (void **) dm = (void *)-2;
}
PETSC_EXTERN void  dmplextransformsetdm_(DMPlexTransform tr,DM dm, int *ierr)
{
CHKFORTRANNULLOBJECT(tr);
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexTransformSetDM(
	(DMPlexTransform)PetscToPointer((tr) ),
	(DM)PetscToPointer((dm) ));
}
PETSC_EXTERN void  dmplextransformgetactive_(DMPlexTransform tr,DMLabel *active, int *ierr)
{
CHKFORTRANNULLOBJECT(tr);
PetscBool active_null = !*(void**) active ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(active);
*ierr = DMPlexTransformGetActive(
	(DMPlexTransform)PetscToPointer((tr) ),active);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! active_null && !*(void**) active) * (void **) active = (void *)-2;
}
PETSC_EXTERN void  dmplextransformsetactive_(DMPlexTransform tr,DMLabel active, int *ierr)
{
CHKFORTRANNULLOBJECT(tr);
CHKFORTRANNULLOBJECT(active);
*ierr = DMPlexTransformSetActive(
	(DMPlexTransform)PetscToPointer((tr) ),
	(DMLabel)PetscToPointer((active) ));
}
PETSC_EXTERN void  dmplextransformsetdimensions_(DMPlexTransform tr,DM dm,DM tdm, int *ierr)
{
CHKFORTRANNULLOBJECT(tr);
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(tdm);
*ierr = DMPlexTransformSetDimensions(
	(DMPlexTransform)PetscToPointer((tr) ),
	(DM)PetscToPointer((dm) ),
	(DM)PetscToPointer((tdm) ));
}
PETSC_EXTERN void  dmplextransformgettargetpoint_(DMPlexTransform tr,DMPolytopeType *ct,DMPolytopeType *ctNew,PetscInt *p,PetscInt *r,PetscInt *pNew, int *ierr)
{
CHKFORTRANNULLOBJECT(tr);
CHKFORTRANNULLINTEGER(pNew);
*ierr = DMPlexTransformGetTargetPoint(
	(DMPlexTransform)PetscToPointer((tr) ),*ct,*ctNew,*p,*r,pNew);
}
PETSC_EXTERN void  dmplextransformgetsourcepoint_(DMPlexTransform tr,PetscInt *pNew,DMPolytopeType *ct,DMPolytopeType *ctNew,PetscInt *p,PetscInt *r, int *ierr)
{
CHKFORTRANNULLOBJECT(tr);
CHKFORTRANNULLINTEGER(p);
CHKFORTRANNULLINTEGER(r);
*ierr = DMPlexTransformGetSourcePoint(
	(DMPlexTransform)PetscToPointer((tr) ),*pNew,ct,ctNew,p,r);
}
PETSC_EXTERN void  dmplextransformcelltransform_(DMPlexTransform tr,DMPolytopeType *source,PetscInt *p,PetscInt *rt,PetscInt *Nt,DMPolytopeType *target[],PetscInt *size[],PetscInt *cone[],PetscInt *ornt[], int *ierr)
{
CHKFORTRANNULLOBJECT(tr);
CHKFORTRANNULLINTEGER(rt);
CHKFORTRANNULLINTEGER(Nt);
*ierr = DMPlexTransformCellTransform(
	(DMPlexTransform)PetscToPointer((tr) ),*source,*p,rt,Nt,target,size,cone,ornt);
}
PETSC_EXTERN void  dmplextransformgetsubcellorientation_(DMPlexTransform tr,DMPolytopeType *sct,PetscInt *sp,PetscInt *so,DMPolytopeType *tct,PetscInt *r,PetscInt *o,PetscInt *rnew,PetscInt *onew, int *ierr)
{
CHKFORTRANNULLOBJECT(tr);
CHKFORTRANNULLINTEGER(rnew);
CHKFORTRANNULLINTEGER(onew);
*ierr = DMPlexTransformGetSubcellOrientation(
	(DMPlexTransform)PetscToPointer((tr) ),*sct,*sp,*so,*tct,*r,*o,rnew,onew);
}
PETSC_EXTERN void  dmplextransformmapcoordinates_(DMPlexTransform tr,DMPolytopeType *pct,DMPolytopeType *ct,PetscInt *p,PetscInt *r,PetscInt *Nv,PetscInt *dE, PetscScalar in[],PetscScalar out[], int *ierr)
{
CHKFORTRANNULLOBJECT(tr);
CHKFORTRANNULLSCALAR(in);
CHKFORTRANNULLSCALAR(out);
*ierr = DMPlexTransformMapCoordinates(
	(DMPlexTransform)PetscToPointer((tr) ),*pct,*ct,*p,*r,*Nv,*dE,in,out);
}
PETSC_EXTERN void  dmplextransformapply_(DMPlexTransform tr,DM dm,DM *tdm, int *ierr)
{
CHKFORTRANNULLOBJECT(tr);
CHKFORTRANNULLOBJECT(dm);
PetscBool tdm_null = !*(void**) tdm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(tdm);
*ierr = DMPlexTransformApply(
	(DMPlexTransform)PetscToPointer((tr) ),
	(DM)PetscToPointer((dm) ),tdm);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! tdm_null && !*(void**) tdm) * (void **) tdm = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
