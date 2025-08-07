#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* dualspace.c */
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

#include "petscfe.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdualspacesettype_ PETSCDUALSPACESETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdualspacesettype_ petscdualspacesettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdualspacegettype_ PETSCDUALSPACEGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdualspacegettype_ petscdualspacegettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdualspaceviewfromoptions_ PETSCDUALSPACEVIEWFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdualspaceviewfromoptions_ petscdualspaceviewfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdualspaceview_ PETSCDUALSPACEVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdualspaceview_ petscdualspaceview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdualspacesetfromoptions_ PETSCDUALSPACESETFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdualspacesetfromoptions_ petscdualspacesetfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdualspacesetup_ PETSCDUALSPACESETUP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdualspacesetup_ petscdualspacesetup
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdualspacedestroy_ PETSCDUALSPACEDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdualspacedestroy_ petscdualspacedestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdualspacecreate_ PETSCDUALSPACECREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdualspacecreate_ petscdualspacecreate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdualspaceduplicate_ PETSCDUALSPACEDUPLICATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdualspaceduplicate_ petscdualspaceduplicate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdualspacegetdm_ PETSCDUALSPACEGETDM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdualspacegetdm_ petscdualspacegetdm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdualspacesetdm_ PETSCDUALSPACESETDM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdualspacesetdm_ petscdualspacesetdm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdualspacegetorder_ PETSCDUALSPACEGETORDER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdualspacegetorder_ petscdualspacegetorder
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdualspacesetorder_ PETSCDUALSPACESETORDER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdualspacesetorder_ petscdualspacesetorder
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdualspacegetnumcomponents_ PETSCDUALSPACEGETNUMCOMPONENTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdualspacegetnumcomponents_ petscdualspacegetnumcomponents
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdualspacesetnumcomponents_ PETSCDUALSPACESETNUMCOMPONENTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdualspacesetnumcomponents_ petscdualspacesetnumcomponents
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdualspacegetfunctional_ PETSCDUALSPACEGETFUNCTIONAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdualspacegetfunctional_ petscdualspacegetfunctional
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdualspacegetdimension_ PETSCDUALSPACEGETDIMENSION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdualspacegetdimension_ petscdualspacegetdimension
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdualspacegetinteriordimension_ PETSCDUALSPACEGETINTERIORDIMENSION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdualspacegetinteriordimension_ petscdualspacegetinteriordimension
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdualspacegetuniform_ PETSCDUALSPACEGETUNIFORM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdualspacegetuniform_ petscdualspacegetuniform
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdualspacegetsection_ PETSCDUALSPACEGETSECTION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdualspacegetsection_ petscdualspacegetsection
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdualspacegetinteriorsection_ PETSCDUALSPACEGETINTERIORSECTION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdualspacegetinteriorsection_ petscdualspacegetinteriorsection
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdualspaceapplyall_ PETSCDUALSPACEAPPLYALL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdualspaceapplyall_ petscdualspaceapplyall
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdualspaceapplyinterior_ PETSCDUALSPACEAPPLYINTERIOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdualspaceapplyinterior_ petscdualspaceapplyinterior
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdualspaceapplyalldefault_ PETSCDUALSPACEAPPLYALLDEFAULT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdualspaceapplyalldefault_ petscdualspaceapplyalldefault
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdualspaceapplyinteriordefault_ PETSCDUALSPACEAPPLYINTERIORDEFAULT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdualspaceapplyinteriordefault_ petscdualspaceapplyinteriordefault
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdualspacegetalldata_ PETSCDUALSPACEGETALLDATA
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdualspacegetalldata_ petscdualspacegetalldata
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdualspacecreatealldatadefault_ PETSCDUALSPACECREATEALLDATADEFAULT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdualspacecreatealldatadefault_ petscdualspacecreatealldatadefault
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdualspacegetinteriordata_ PETSCDUALSPACEGETINTERIORDATA
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdualspacegetinteriordata_ petscdualspacegetinteriordata
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdualspacecreateinteriordatadefault_ PETSCDUALSPACECREATEINTERIORDATADEFAULT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdualspacecreateinteriordatadefault_ petscdualspacecreateinteriordatadefault
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdualspaceequal_ PETSCDUALSPACEEQUAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdualspaceequal_ petscdualspaceequal
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdualspacegetheightsubspace_ PETSCDUALSPACEGETHEIGHTSUBSPACE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdualspacegetheightsubspace_ petscdualspacegetheightsubspace
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdualspacegetpointsubspace_ PETSCDUALSPACEGETPOINTSUBSPACE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdualspacegetpointsubspace_ petscdualspacegetpointsubspace
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdualspacegetformdegree_ PETSCDUALSPACEGETFORMDEGREE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdualspacegetformdegree_ petscdualspacegetformdegree
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdualspacesetformdegree_ PETSCDUALSPACESETFORMDEGREE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdualspacesetformdegree_ petscdualspacesetformdegree
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdualspacegetderahm_ PETSCDUALSPACEGETDERAHM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdualspacegetderahm_ petscdualspacegetderahm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdualspacetransform_ PETSCDUALSPACETRANSFORM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdualspacetransform_ petscdualspacetransform
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdualspacetransformgradient_ PETSCDUALSPACETRANSFORMGRADIENT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdualspacetransformgradient_ petscdualspacetransformgradient
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdualspacetransformhessian_ PETSCDUALSPACETRANSFORMHESSIAN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdualspacetransformhessian_ petscdualspacetransformhessian
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdualspacepullback_ PETSCDUALSPACEPULLBACK
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdualspacepullback_ petscdualspacepullback
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdualspacepushforward_ PETSCDUALSPACEPUSHFORWARD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdualspacepushforward_ petscdualspacepushforward
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdualspacepushforwardgradient_ PETSCDUALSPACEPUSHFORWARDGRADIENT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdualspacepushforwardgradient_ petscdualspacepushforwardgradient
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdualspacepushforwardhessian_ PETSCDUALSPACEPUSHFORWARDHESSIAN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdualspacepushforwardhessian_ petscdualspacepushforwardhessian
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscdualspacesettype_(PetscDualSpace sp,char *name, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(sp);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PetscDualSpaceSetType(
	(PetscDualSpace)PetscToPointer((sp) ),_cltmp0);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  petscdualspacegettype_(PetscDualSpace sp,char *name, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(sp);
*ierr = PetscDualSpaceGetType(
	(PetscDualSpace)PetscToPointer((sp) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for name */
*ierr = PetscStrncpy(name, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, name, cl0);
}
PETSC_EXTERN void  petscdualspaceviewfromoptions_(PetscDualSpace A,PetscObject obj, char name[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(obj);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PetscDualSpaceViewFromOptions(
	(PetscDualSpace)PetscToPointer((A) ),
	(PetscObject)PetscToPointer((obj) ),_cltmp0);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  petscdualspaceview_(PetscDualSpace sp,PetscViewer v, int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
CHKFORTRANNULLOBJECT(v);
*ierr = PetscDualSpaceView(
	(PetscDualSpace)PetscToPointer((sp) ),PetscPatchDefaultViewers((PetscViewer*)v));
}
PETSC_EXTERN void  petscdualspacesetfromoptions_(PetscDualSpace sp, int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
*ierr = PetscDualSpaceSetFromOptions(
	(PetscDualSpace)PetscToPointer((sp) ));
}
PETSC_EXTERN void  petscdualspacesetup_(PetscDualSpace sp, int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
*ierr = PetscDualSpaceSetUp(
	(PetscDualSpace)PetscToPointer((sp) ));
}
PETSC_EXTERN void  petscdualspacedestroy_(PetscDualSpace *sp, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(sp);
 PetscBool sp_null = !*(void**) sp ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(sp);
*ierr = PetscDualSpaceDestroy(sp);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! sp_null && !*(void**) sp) * (void **) sp = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(sp);
 }
PETSC_EXTERN void  petscdualspacecreate_(MPI_Fint * comm,PetscDualSpace *sp, int *ierr)
{
PETSC_FORTRAN_OBJECT_CREATE(sp);
 PetscBool sp_null = !*(void**) sp ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(sp);
*ierr = PetscDualSpaceCreate(
	MPI_Comm_f2c(*(comm)),sp);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! sp_null && !*(void**) sp) * (void **) sp = (void *)-2;
}
PETSC_EXTERN void  petscdualspaceduplicate_(PetscDualSpace sp,PetscDualSpace *spNew, int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
PetscBool spNew_null = !*(void**) spNew ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(spNew);
*ierr = PetscDualSpaceDuplicate(
	(PetscDualSpace)PetscToPointer((sp) ),spNew);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! spNew_null && !*(void**) spNew) * (void **) spNew = (void *)-2;
}
PETSC_EXTERN void  petscdualspacegetdm_(PetscDualSpace sp,DM *dm, int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
PetscBool dm_null = !*(void**) dm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dm);
*ierr = PetscDualSpaceGetDM(
	(PetscDualSpace)PetscToPointer((sp) ),dm);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dm_null && !*(void**) dm) * (void **) dm = (void *)-2;
}
PETSC_EXTERN void  petscdualspacesetdm_(PetscDualSpace sp,DM dm, int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
CHKFORTRANNULLOBJECT(dm);
*ierr = PetscDualSpaceSetDM(
	(PetscDualSpace)PetscToPointer((sp) ),
	(DM)PetscToPointer((dm) ));
}
PETSC_EXTERN void  petscdualspacegetorder_(PetscDualSpace sp,PetscInt *order, int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
CHKFORTRANNULLINTEGER(order);
*ierr = PetscDualSpaceGetOrder(
	(PetscDualSpace)PetscToPointer((sp) ),order);
}
PETSC_EXTERN void  petscdualspacesetorder_(PetscDualSpace sp,PetscInt *order, int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
*ierr = PetscDualSpaceSetOrder(
	(PetscDualSpace)PetscToPointer((sp) ),*order);
}
PETSC_EXTERN void  petscdualspacegetnumcomponents_(PetscDualSpace sp,PetscInt *Nc, int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
CHKFORTRANNULLINTEGER(Nc);
*ierr = PetscDualSpaceGetNumComponents(
	(PetscDualSpace)PetscToPointer((sp) ),Nc);
}
PETSC_EXTERN void  petscdualspacesetnumcomponents_(PetscDualSpace sp,PetscInt *Nc, int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
*ierr = PetscDualSpaceSetNumComponents(
	(PetscDualSpace)PetscToPointer((sp) ),*Nc);
}
PETSC_EXTERN void  petscdualspacegetfunctional_(PetscDualSpace sp,PetscInt *i,PetscQuadrature *functional, int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
PetscBool functional_null = !*(void**) functional ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(functional);
*ierr = PetscDualSpaceGetFunctional(
	(PetscDualSpace)PetscToPointer((sp) ),*i,functional);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! functional_null && !*(void**) functional) * (void **) functional = (void *)-2;
}
PETSC_EXTERN void  petscdualspacegetdimension_(PetscDualSpace sp,PetscInt *dim, int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
CHKFORTRANNULLINTEGER(dim);
*ierr = PetscDualSpaceGetDimension(
	(PetscDualSpace)PetscToPointer((sp) ),dim);
}
PETSC_EXTERN void  petscdualspacegetinteriordimension_(PetscDualSpace sp,PetscInt *intdim, int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
CHKFORTRANNULLINTEGER(intdim);
*ierr = PetscDualSpaceGetInteriorDimension(
	(PetscDualSpace)PetscToPointer((sp) ),intdim);
}
PETSC_EXTERN void  petscdualspacegetuniform_(PetscDualSpace sp,PetscBool *uniform, int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
*ierr = PetscDualSpaceGetUniform(
	(PetscDualSpace)PetscToPointer((sp) ),uniform);
}
PETSC_EXTERN void  petscdualspacegetsection_(PetscDualSpace sp,PetscSection *section, int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
PetscBool section_null = !*(void**) section ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(section);
*ierr = PetscDualSpaceGetSection(
	(PetscDualSpace)PetscToPointer((sp) ),section);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! section_null && !*(void**) section) * (void **) section = (void *)-2;
}
PETSC_EXTERN void  petscdualspacegetinteriorsection_(PetscDualSpace sp,PetscSection *section, int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
PetscBool section_null = !*(void**) section ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(section);
*ierr = PetscDualSpaceGetInteriorSection(
	(PetscDualSpace)PetscToPointer((sp) ),section);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! section_null && !*(void**) section) * (void **) section = (void *)-2;
}
PETSC_EXTERN void  petscdualspaceapplyall_(PetscDualSpace sp, PetscScalar *pointEval,PetscScalar *spValue, int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
CHKFORTRANNULLSCALAR(pointEval);
CHKFORTRANNULLSCALAR(spValue);
*ierr = PetscDualSpaceApplyAll(
	(PetscDualSpace)PetscToPointer((sp) ),pointEval,spValue);
}
PETSC_EXTERN void  petscdualspaceapplyinterior_(PetscDualSpace sp, PetscScalar *pointEval,PetscScalar *spValue, int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
CHKFORTRANNULLSCALAR(pointEval);
CHKFORTRANNULLSCALAR(spValue);
*ierr = PetscDualSpaceApplyInterior(
	(PetscDualSpace)PetscToPointer((sp) ),pointEval,spValue);
}
PETSC_EXTERN void  petscdualspaceapplyalldefault_(PetscDualSpace sp, PetscScalar *pointEval,PetscScalar *spValue, int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
CHKFORTRANNULLSCALAR(pointEval);
CHKFORTRANNULLSCALAR(spValue);
*ierr = PetscDualSpaceApplyAllDefault(
	(PetscDualSpace)PetscToPointer((sp) ),pointEval,spValue);
}
PETSC_EXTERN void  petscdualspaceapplyinteriordefault_(PetscDualSpace sp, PetscScalar *pointEval,PetscScalar *spValue, int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
CHKFORTRANNULLSCALAR(pointEval);
CHKFORTRANNULLSCALAR(spValue);
*ierr = PetscDualSpaceApplyInteriorDefault(
	(PetscDualSpace)PetscToPointer((sp) ),pointEval,spValue);
}
PETSC_EXTERN void  petscdualspacegetalldata_(PetscDualSpace sp,PetscQuadrature *allNodes,Mat *allMat, int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
PetscBool allNodes_null = !*(void**) allNodes ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(allNodes);
PetscBool allMat_null = !*(void**) allMat ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(allMat);
*ierr = PetscDualSpaceGetAllData(
	(PetscDualSpace)PetscToPointer((sp) ),allNodes,allMat);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! allNodes_null && !*(void**) allNodes) * (void **) allNodes = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! allMat_null && !*(void**) allMat) * (void **) allMat = (void *)-2;
}
PETSC_EXTERN void  petscdualspacecreatealldatadefault_(PetscDualSpace sp,PetscQuadrature *allNodes,Mat *allMat, int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
PetscBool allNodes_null = !*(void**) allNodes ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(allNodes);
PetscBool allMat_null = !*(void**) allMat ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(allMat);
*ierr = PetscDualSpaceCreateAllDataDefault(
	(PetscDualSpace)PetscToPointer((sp) ),allNodes,allMat);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! allNodes_null && !*(void**) allNodes) * (void **) allNodes = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! allMat_null && !*(void**) allMat) * (void **) allMat = (void *)-2;
}
PETSC_EXTERN void  petscdualspacegetinteriordata_(PetscDualSpace sp,PetscQuadrature *intNodes,Mat *intMat, int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
PetscBool intNodes_null = !*(void**) intNodes ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(intNodes);
PetscBool intMat_null = !*(void**) intMat ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(intMat);
*ierr = PetscDualSpaceGetInteriorData(
	(PetscDualSpace)PetscToPointer((sp) ),intNodes,intMat);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! intNodes_null && !*(void**) intNodes) * (void **) intNodes = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! intMat_null && !*(void**) intMat) * (void **) intMat = (void *)-2;
}
PETSC_EXTERN void  petscdualspacecreateinteriordatadefault_(PetscDualSpace sp,PetscQuadrature *intNodes,Mat *intMat, int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
PetscBool intNodes_null = !*(void**) intNodes ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(intNodes);
PetscBool intMat_null = !*(void**) intMat ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(intMat);
*ierr = PetscDualSpaceCreateInteriorDataDefault(
	(PetscDualSpace)PetscToPointer((sp) ),intNodes,intMat);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! intNodes_null && !*(void**) intNodes) * (void **) intNodes = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! intMat_null && !*(void**) intMat) * (void **) intMat = (void *)-2;
}
PETSC_EXTERN void  petscdualspaceequal_(PetscDualSpace A,PetscDualSpace B,PetscBool *equal, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(B);
*ierr = PetscDualSpaceEqual(
	(PetscDualSpace)PetscToPointer((A) ),
	(PetscDualSpace)PetscToPointer((B) ),equal);
}
PETSC_EXTERN void  petscdualspacegetheightsubspace_(PetscDualSpace sp,PetscInt *height,PetscDualSpace *subsp, int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
PetscBool subsp_null = !*(void**) subsp ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(subsp);
*ierr = PetscDualSpaceGetHeightSubspace(
	(PetscDualSpace)PetscToPointer((sp) ),*height,subsp);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! subsp_null && !*(void**) subsp) * (void **) subsp = (void *)-2;
}
PETSC_EXTERN void  petscdualspacegetpointsubspace_(PetscDualSpace sp,PetscInt *point,PetscDualSpace *bdsp, int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
PetscBool bdsp_null = !*(void**) bdsp ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(bdsp);
*ierr = PetscDualSpaceGetPointSubspace(
	(PetscDualSpace)PetscToPointer((sp) ),*point,bdsp);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! bdsp_null && !*(void**) bdsp) * (void **) bdsp = (void *)-2;
}
PETSC_EXTERN void  petscdualspacegetformdegree_(PetscDualSpace dsp,PetscInt *k, int *ierr)
{
CHKFORTRANNULLOBJECT(dsp);
CHKFORTRANNULLINTEGER(k);
*ierr = PetscDualSpaceGetFormDegree(
	(PetscDualSpace)PetscToPointer((dsp) ),k);
}
PETSC_EXTERN void  petscdualspacesetformdegree_(PetscDualSpace dsp,PetscInt *k, int *ierr)
{
CHKFORTRANNULLOBJECT(dsp);
*ierr = PetscDualSpaceSetFormDegree(
	(PetscDualSpace)PetscToPointer((dsp) ),*k);
}
PETSC_EXTERN void  petscdualspacegetderahm_(PetscDualSpace dsp,PetscInt *k, int *ierr)
{
CHKFORTRANNULLOBJECT(dsp);
CHKFORTRANNULLINTEGER(k);
*ierr = PetscDualSpaceGetDeRahm(
	(PetscDualSpace)PetscToPointer((dsp) ),k);
}
PETSC_EXTERN void  petscdualspacetransform_(PetscDualSpace dsp,PetscDualSpaceTransformType *trans,PetscBool *isInverse,PetscFEGeom *fegeom,PetscInt *Nv,PetscInt *Nc,PetscScalar vals[], int *ierr)
{
CHKFORTRANNULLOBJECT(dsp);
CHKFORTRANNULLSCALAR(vals);
*ierr = PetscDualSpaceTransform(
	(PetscDualSpace)PetscToPointer((dsp) ),*trans,*isInverse,
	(PetscFEGeom* )PetscToPointer((fegeom) ),*Nv,*Nc,vals);
}
PETSC_EXTERN void  petscdualspacetransformgradient_(PetscDualSpace dsp,PetscDualSpaceTransformType *trans,PetscBool *isInverse,PetscFEGeom *fegeom,PetscInt *Nv,PetscInt *Nc,PetscScalar vals[], int *ierr)
{
CHKFORTRANNULLOBJECT(dsp);
CHKFORTRANNULLSCALAR(vals);
*ierr = PetscDualSpaceTransformGradient(
	(PetscDualSpace)PetscToPointer((dsp) ),*trans,*isInverse,
	(PetscFEGeom* )PetscToPointer((fegeom) ),*Nv,*Nc,vals);
}
PETSC_EXTERN void  petscdualspacetransformhessian_(PetscDualSpace dsp,PetscDualSpaceTransformType *trans,PetscBool *isInverse,PetscFEGeom *fegeom,PetscInt *Nv,PetscInt *Nc,PetscScalar vals[], int *ierr)
{
CHKFORTRANNULLOBJECT(dsp);
CHKFORTRANNULLSCALAR(vals);
*ierr = PetscDualSpaceTransformHessian(
	(PetscDualSpace)PetscToPointer((dsp) ),*trans,*isInverse,
	(PetscFEGeom* )PetscToPointer((fegeom) ),*Nv,*Nc,vals);
}
PETSC_EXTERN void  petscdualspacepullback_(PetscDualSpace dsp,PetscFEGeom *fegeom,PetscInt *Nq,PetscInt *Nc,PetscScalar pointEval[], int *ierr)
{
CHKFORTRANNULLOBJECT(dsp);
CHKFORTRANNULLSCALAR(pointEval);
*ierr = PetscDualSpacePullback(
	(PetscDualSpace)PetscToPointer((dsp) ),
	(PetscFEGeom* )PetscToPointer((fegeom) ),*Nq,*Nc,pointEval);
}
PETSC_EXTERN void  petscdualspacepushforward_(PetscDualSpace dsp,PetscFEGeom *fegeom,PetscInt *Nq,PetscInt *Nc,PetscScalar pointEval[], int *ierr)
{
CHKFORTRANNULLOBJECT(dsp);
CHKFORTRANNULLSCALAR(pointEval);
*ierr = PetscDualSpacePushforward(
	(PetscDualSpace)PetscToPointer((dsp) ),
	(PetscFEGeom* )PetscToPointer((fegeom) ),*Nq,*Nc,pointEval);
}
PETSC_EXTERN void  petscdualspacepushforwardgradient_(PetscDualSpace dsp,PetscFEGeom *fegeom,PetscInt *Nq,PetscInt *Nc,PetscScalar pointEval[], int *ierr)
{
CHKFORTRANNULLOBJECT(dsp);
CHKFORTRANNULLSCALAR(pointEval);
*ierr = PetscDualSpacePushforwardGradient(
	(PetscDualSpace)PetscToPointer((dsp) ),
	(PetscFEGeom* )PetscToPointer((fegeom) ),*Nq,*Nc,pointEval);
}
PETSC_EXTERN void  petscdualspacepushforwardhessian_(PetscDualSpace dsp,PetscFEGeom *fegeom,PetscInt *Nq,PetscInt *Nc,PetscScalar pointEval[], int *ierr)
{
CHKFORTRANNULLOBJECT(dsp);
CHKFORTRANNULLSCALAR(pointEval);
*ierr = PetscDualSpacePushforwardHessian(
	(PetscDualSpace)PetscToPointer((dsp) ),
	(PetscFEGeom* )PetscToPointer((fegeom) ),*Nq,*Nc,pointEval);
}
#if defined(__cplusplus)
}
#endif
