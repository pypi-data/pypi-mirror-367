#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* dtds.c */
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

#include "petscds.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdssettype_ PETSCDSSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdssettype_ petscdssettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdsgettype_ PETSCDSGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdsgettype_ petscdsgettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdsviewfromoptions_ PETSCDSVIEWFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdsviewfromoptions_ petscdsviewfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdsview_ PETSCDSVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdsview_ petscdsview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdssetfromoptions_ PETSCDSSETFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdssetfromoptions_ petscdssetfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdssetup_ PETSCDSSETUP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdssetup_ petscdssetup
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdsdestroy_ PETSCDSDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdsdestroy_ petscdsdestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdscreate_ PETSCDSCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdscreate_ petscdscreate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdsgetnumfields_ PETSCDSGETNUMFIELDS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdsgetnumfields_ petscdsgetnumfields
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdsgetspatialdimension_ PETSCDSGETSPATIALDIMENSION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdsgetspatialdimension_ petscdsgetspatialdimension
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdsgetcoordinatedimension_ PETSCDSGETCOORDINATEDIMENSION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdsgetcoordinatedimension_ petscdsgetcoordinatedimension
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdssetcoordinatedimension_ PETSCDSSETCOORDINATEDIMENSION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdssetcoordinatedimension_ petscdssetcoordinatedimension
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdsgetforcequad_ PETSCDSGETFORCEQUAD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdsgetforcequad_ petscdsgetforcequad
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdssetforcequad_ PETSCDSSETFORCEQUAD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdssetforcequad_ petscdssetforcequad
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdsiscohesive_ PETSCDSISCOHESIVE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdsiscohesive_ petscdsiscohesive
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdsgetnumcohesive_ PETSCDSGETNUMCOHESIVE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdsgetnumcohesive_ petscdsgetnumcohesive
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdsgetcohesive_ PETSCDSGETCOHESIVE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdsgetcohesive_ petscdsgetcohesive
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdssetcohesive_ PETSCDSSETCOHESIVE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdssetcohesive_ petscdssetcohesive
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdsgettotaldimension_ PETSCDSGETTOTALDIMENSION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdsgettotaldimension_ petscdsgettotaldimension
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdsgettotalcomponents_ PETSCDSGETTOTALCOMPONENTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdsgettotalcomponents_ petscdsgettotalcomponents
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdsgetdiscretization_ PETSCDSGETDISCRETIZATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdsgetdiscretization_ petscdsgetdiscretization
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdssetdiscretization_ PETSCDSSETDISCRETIZATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdssetdiscretization_ petscdssetdiscretization
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdsgetweakform_ PETSCDSGETWEAKFORM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdsgetweakform_ petscdsgetweakform
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdssetweakform_ PETSCDSSETWEAKFORM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdssetweakform_ petscdssetweakform
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdsadddiscretization_ PETSCDSADDDISCRETIZATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdsadddiscretization_ petscdsadddiscretization
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdsgetquadrature_ PETSCDSGETQUADRATURE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdsgetquadrature_ petscdsgetquadrature
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdsgetimplicit_ PETSCDSGETIMPLICIT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdsgetimplicit_ petscdsgetimplicit
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdssetimplicit_ PETSCDSSETIMPLICIT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdssetimplicit_ petscdssetimplicit
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdsgetjetdegree_ PETSCDSGETJETDEGREE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdsgetjetdegree_ petscdsgetjetdegree
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdssetjetdegree_ PETSCDSSETJETDEGREE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdssetjetdegree_ petscdssetjetdegree
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdshasjacobian_ PETSCDSHASJACOBIAN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdshasjacobian_ petscdshasjacobian
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdsusejacobianpreconditioner_ PETSCDSUSEJACOBIANPRECONDITIONER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdsusejacobianpreconditioner_ petscdsusejacobianpreconditioner
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdshasjacobianpreconditioner_ PETSCDSHASJACOBIANPRECONDITIONER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdshasjacobianpreconditioner_ petscdshasjacobianpreconditioner
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdshasdynamicjacobian_ PETSCDSHASDYNAMICJACOBIAN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdshasdynamicjacobian_ petscdshasdynamicjacobian
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdshasbdjacobian_ PETSCDSHASBDJACOBIAN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdshasbdjacobian_ petscdshasbdjacobian
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdshasbdjacobianpreconditioner_ PETSCDSHASBDJACOBIANPRECONDITIONER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdshasbdjacobianpreconditioner_ petscdshasbdjacobianpreconditioner
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdsgetfieldindex_ PETSCDSGETFIELDINDEX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdsgetfieldindex_ petscdsgetfieldindex
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdsgetfieldsize_ PETSCDSGETFIELDSIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdsgetfieldsize_ petscdsgetfieldsize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdsgetfieldoffset_ PETSCDSGETFIELDOFFSET
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdsgetfieldoffset_ petscdsgetfieldoffset
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdsgetfieldoffsetcohesive_ PETSCDSGETFIELDOFFSETCOHESIVE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdsgetfieldoffsetcohesive_ petscdsgetfieldoffsetcohesive
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdsgetdimensions_ PETSCDSGETDIMENSIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdsgetdimensions_ petscdsgetdimensions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdsgetcomponents_ PETSCDSGETCOMPONENTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdsgetcomponents_ petscdsgetcomponents
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdsgetcomponentoffset_ PETSCDSGETCOMPONENTOFFSET
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdsgetcomponentoffset_ petscdsgetcomponentoffset
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdsgetcomponentoffsets_ PETSCDSGETCOMPONENTOFFSETS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdsgetcomponentoffsets_ petscdsgetcomponentoffsets
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdsgetcomponentderivativeoffsets_ PETSCDSGETCOMPONENTDERIVATIVEOFFSETS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdsgetcomponentderivativeoffsets_ petscdsgetcomponentderivativeoffsets
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdsgetcomponentoffsetscohesive_ PETSCDSGETCOMPONENTOFFSETSCOHESIVE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdsgetcomponentoffsetscohesive_ petscdsgetcomponentoffsetscohesive
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdsgetcomponentderivativeoffsetscohesive_ PETSCDSGETCOMPONENTDERIVATIVEOFFSETSCOHESIVE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdsgetcomponentderivativeoffsetscohesive_ petscdsgetcomponentderivativeoffsetscohesive
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdsgetnumboundary_ PETSCDSGETNUMBOUNDARY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdsgetnumboundary_ petscdsgetnumboundary
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdsupdateboundarylabels_ PETSCDSUPDATEBOUNDARYLABELS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdsupdateboundarylabels_ petscdsupdateboundarylabels
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdscopyboundary_ PETSCDSCOPYBOUNDARY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdscopyboundary_ petscdscopyboundary
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdsdestroyboundary_ PETSCDSDESTROYBOUNDARY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdsdestroyboundary_ petscdsdestroyboundary
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdsselectdiscretizations_ PETSCDSSELECTDISCRETIZATIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdsselectdiscretizations_ petscdsselectdiscretizations
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdsselectequations_ PETSCDSSELECTEQUATIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdsselectequations_ petscdsselectequations
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdscopyequations_ PETSCDSCOPYEQUATIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdscopyequations_ petscdscopyequations
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdscopyconstants_ PETSCDSCOPYCONSTANTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdscopyconstants_ petscdscopyconstants
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscdscopyexactsolutions_ PETSCDSCOPYEXACTSOLUTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscdscopyexactsolutions_ petscdscopyexactsolutions
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscdssettype_(PetscDS prob,char *name, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(prob);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PetscDSSetType(
	(PetscDS)PetscToPointer((prob) ),_cltmp0);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  petscdsgettype_(PetscDS prob,char *name, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(prob);
*ierr = PetscDSGetType(
	(PetscDS)PetscToPointer((prob) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for name */
*ierr = PetscStrncpy(name, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, name, cl0);
}
PETSC_EXTERN void  petscdsviewfromoptions_(PetscDS A,PetscObject obj, char name[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(obj);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PetscDSViewFromOptions(
	(PetscDS)PetscToPointer((A) ),
	(PetscObject)PetscToPointer((obj) ),_cltmp0);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  petscdsview_(PetscDS prob,PetscViewer v, int *ierr)
{
CHKFORTRANNULLOBJECT(prob);
CHKFORTRANNULLOBJECT(v);
*ierr = PetscDSView(
	(PetscDS)PetscToPointer((prob) ),PetscPatchDefaultViewers((PetscViewer*)v));
}
PETSC_EXTERN void  petscdssetfromoptions_(PetscDS prob, int *ierr)
{
CHKFORTRANNULLOBJECT(prob);
*ierr = PetscDSSetFromOptions(
	(PetscDS)PetscToPointer((prob) ));
}
PETSC_EXTERN void  petscdssetup_(PetscDS prob, int *ierr)
{
CHKFORTRANNULLOBJECT(prob);
*ierr = PetscDSSetUp(
	(PetscDS)PetscToPointer((prob) ));
}
PETSC_EXTERN void  petscdsdestroy_(PetscDS *ds, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(ds);
 PetscBool ds_null = !*(void**) ds ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(ds);
*ierr = PetscDSDestroy(ds);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! ds_null && !*(void**) ds) * (void **) ds = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(ds);
 }
PETSC_EXTERN void  petscdscreate_(MPI_Fint * comm,PetscDS *ds, int *ierr)
{
PETSC_FORTRAN_OBJECT_CREATE(ds);
 PetscBool ds_null = !*(void**) ds ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(ds);
*ierr = PetscDSCreate(
	MPI_Comm_f2c(*(comm)),ds);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! ds_null && !*(void**) ds) * (void **) ds = (void *)-2;
}
PETSC_EXTERN void  petscdsgetnumfields_(PetscDS prob,PetscInt *Nf, int *ierr)
{
CHKFORTRANNULLOBJECT(prob);
CHKFORTRANNULLINTEGER(Nf);
*ierr = PetscDSGetNumFields(
	(PetscDS)PetscToPointer((prob) ),Nf);
}
PETSC_EXTERN void  petscdsgetspatialdimension_(PetscDS prob,PetscInt *dim, int *ierr)
{
CHKFORTRANNULLOBJECT(prob);
CHKFORTRANNULLINTEGER(dim);
*ierr = PetscDSGetSpatialDimension(
	(PetscDS)PetscToPointer((prob) ),dim);
}
PETSC_EXTERN void  petscdsgetcoordinatedimension_(PetscDS prob,PetscInt *dimEmbed, int *ierr)
{
CHKFORTRANNULLOBJECT(prob);
CHKFORTRANNULLINTEGER(dimEmbed);
*ierr = PetscDSGetCoordinateDimension(
	(PetscDS)PetscToPointer((prob) ),dimEmbed);
}
PETSC_EXTERN void  petscdssetcoordinatedimension_(PetscDS prob,PetscInt *dimEmbed, int *ierr)
{
CHKFORTRANNULLOBJECT(prob);
*ierr = PetscDSSetCoordinateDimension(
	(PetscDS)PetscToPointer((prob) ),*dimEmbed);
}
PETSC_EXTERN void  petscdsgetforcequad_(PetscDS ds,PetscBool *forceQuad, int *ierr)
{
CHKFORTRANNULLOBJECT(ds);
*ierr = PetscDSGetForceQuad(
	(PetscDS)PetscToPointer((ds) ),forceQuad);
}
PETSC_EXTERN void  petscdssetforcequad_(PetscDS ds,PetscBool *forceQuad, int *ierr)
{
CHKFORTRANNULLOBJECT(ds);
*ierr = PetscDSSetForceQuad(
	(PetscDS)PetscToPointer((ds) ),*forceQuad);
}
PETSC_EXTERN void  petscdsiscohesive_(PetscDS ds,PetscBool *isCohesive, int *ierr)
{
CHKFORTRANNULLOBJECT(ds);
*ierr = PetscDSIsCohesive(
	(PetscDS)PetscToPointer((ds) ),isCohesive);
}
PETSC_EXTERN void  petscdsgetnumcohesive_(PetscDS ds,PetscInt *numCohesive, int *ierr)
{
CHKFORTRANNULLOBJECT(ds);
CHKFORTRANNULLINTEGER(numCohesive);
*ierr = PetscDSGetNumCohesive(
	(PetscDS)PetscToPointer((ds) ),numCohesive);
}
PETSC_EXTERN void  petscdsgetcohesive_(PetscDS ds,PetscInt *f,PetscBool *isCohesive, int *ierr)
{
CHKFORTRANNULLOBJECT(ds);
*ierr = PetscDSGetCohesive(
	(PetscDS)PetscToPointer((ds) ),*f,isCohesive);
}
PETSC_EXTERN void  petscdssetcohesive_(PetscDS ds,PetscInt *f,PetscBool *isCohesive, int *ierr)
{
CHKFORTRANNULLOBJECT(ds);
*ierr = PetscDSSetCohesive(
	(PetscDS)PetscToPointer((ds) ),*f,*isCohesive);
}
PETSC_EXTERN void  petscdsgettotaldimension_(PetscDS prob,PetscInt *dim, int *ierr)
{
CHKFORTRANNULLOBJECT(prob);
CHKFORTRANNULLINTEGER(dim);
*ierr = PetscDSGetTotalDimension(
	(PetscDS)PetscToPointer((prob) ),dim);
}
PETSC_EXTERN void  petscdsgettotalcomponents_(PetscDS prob,PetscInt *Nc, int *ierr)
{
CHKFORTRANNULLOBJECT(prob);
CHKFORTRANNULLINTEGER(Nc);
*ierr = PetscDSGetTotalComponents(
	(PetscDS)PetscToPointer((prob) ),Nc);
}
PETSC_EXTERN void  petscdsgetdiscretization_(PetscDS prob,PetscInt *f,PetscObject *disc, int *ierr)
{
CHKFORTRANNULLOBJECT(prob);
PetscBool disc_null = !*(void**) disc ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(disc);
*ierr = PetscDSGetDiscretization(
	(PetscDS)PetscToPointer((prob) ),*f,disc);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! disc_null && !*(void**) disc) * (void **) disc = (void *)-2;
}
PETSC_EXTERN void  petscdssetdiscretization_(PetscDS prob,PetscInt *f,PetscObject disc, int *ierr)
{
CHKFORTRANNULLOBJECT(prob);
CHKFORTRANNULLOBJECT(disc);
*ierr = PetscDSSetDiscretization(
	(PetscDS)PetscToPointer((prob) ),*f,
	(PetscObject)PetscToPointer((disc) ));
}
PETSC_EXTERN void  petscdsgetweakform_(PetscDS ds,PetscWeakForm *wf, int *ierr)
{
CHKFORTRANNULLOBJECT(ds);
PetscBool wf_null = !*(void**) wf ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(wf);
*ierr = PetscDSGetWeakForm(
	(PetscDS)PetscToPointer((ds) ),wf);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! wf_null && !*(void**) wf) * (void **) wf = (void *)-2;
}
PETSC_EXTERN void  petscdssetweakform_(PetscDS ds,PetscWeakForm wf, int *ierr)
{
CHKFORTRANNULLOBJECT(ds);
CHKFORTRANNULLOBJECT(wf);
*ierr = PetscDSSetWeakForm(
	(PetscDS)PetscToPointer((ds) ),
	(PetscWeakForm)PetscToPointer((wf) ));
}
PETSC_EXTERN void  petscdsadddiscretization_(PetscDS prob,PetscObject disc, int *ierr)
{
CHKFORTRANNULLOBJECT(prob);
CHKFORTRANNULLOBJECT(disc);
*ierr = PetscDSAddDiscretization(
	(PetscDS)PetscToPointer((prob) ),
	(PetscObject)PetscToPointer((disc) ));
}
PETSC_EXTERN void  petscdsgetquadrature_(PetscDS prob,PetscQuadrature *q, int *ierr)
{
CHKFORTRANNULLOBJECT(prob);
PetscBool q_null = !*(void**) q ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(q);
*ierr = PetscDSGetQuadrature(
	(PetscDS)PetscToPointer((prob) ),q);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! q_null && !*(void**) q) * (void **) q = (void *)-2;
}
PETSC_EXTERN void  petscdsgetimplicit_(PetscDS prob,PetscInt *f,PetscBool *implicit, int *ierr)
{
CHKFORTRANNULLOBJECT(prob);
*ierr = PetscDSGetImplicit(
	(PetscDS)PetscToPointer((prob) ),*f,implicit);
}
PETSC_EXTERN void  petscdssetimplicit_(PetscDS prob,PetscInt *f,PetscBool *implicit, int *ierr)
{
CHKFORTRANNULLOBJECT(prob);
*ierr = PetscDSSetImplicit(
	(PetscDS)PetscToPointer((prob) ),*f,*implicit);
}
PETSC_EXTERN void  petscdsgetjetdegree_(PetscDS ds,PetscInt *f,PetscInt *k, int *ierr)
{
CHKFORTRANNULLOBJECT(ds);
CHKFORTRANNULLINTEGER(k);
*ierr = PetscDSGetJetDegree(
	(PetscDS)PetscToPointer((ds) ),*f,k);
}
PETSC_EXTERN void  petscdssetjetdegree_(PetscDS ds,PetscInt *f,PetscInt *k, int *ierr)
{
CHKFORTRANNULLOBJECT(ds);
*ierr = PetscDSSetJetDegree(
	(PetscDS)PetscToPointer((ds) ),*f,*k);
}
PETSC_EXTERN void  petscdshasjacobian_(PetscDS ds,PetscBool *hasJac, int *ierr)
{
CHKFORTRANNULLOBJECT(ds);
*ierr = PetscDSHasJacobian(
	(PetscDS)PetscToPointer((ds) ),hasJac);
}
PETSC_EXTERN void  petscdsusejacobianpreconditioner_(PetscDS prob,PetscBool *useJacPre, int *ierr)
{
CHKFORTRANNULLOBJECT(prob);
*ierr = PetscDSUseJacobianPreconditioner(
	(PetscDS)PetscToPointer((prob) ),*useJacPre);
}
PETSC_EXTERN void  petscdshasjacobianpreconditioner_(PetscDS ds,PetscBool *hasJacPre, int *ierr)
{
CHKFORTRANNULLOBJECT(ds);
*ierr = PetscDSHasJacobianPreconditioner(
	(PetscDS)PetscToPointer((ds) ),hasJacPre);
}
PETSC_EXTERN void  petscdshasdynamicjacobian_(PetscDS ds,PetscBool *hasDynJac, int *ierr)
{
CHKFORTRANNULLOBJECT(ds);
*ierr = PetscDSHasDynamicJacobian(
	(PetscDS)PetscToPointer((ds) ),hasDynJac);
}
PETSC_EXTERN void  petscdshasbdjacobian_(PetscDS ds,PetscBool *hasBdJac, int *ierr)
{
CHKFORTRANNULLOBJECT(ds);
*ierr = PetscDSHasBdJacobian(
	(PetscDS)PetscToPointer((ds) ),hasBdJac);
}
PETSC_EXTERN void  petscdshasbdjacobianpreconditioner_(PetscDS ds,PetscBool *hasBdJacPre, int *ierr)
{
CHKFORTRANNULLOBJECT(ds);
*ierr = PetscDSHasBdJacobianPreconditioner(
	(PetscDS)PetscToPointer((ds) ),hasBdJacPre);
}
PETSC_EXTERN void  petscdsgetfieldindex_(PetscDS prob,PetscObject disc,PetscInt *f, int *ierr)
{
CHKFORTRANNULLOBJECT(prob);
CHKFORTRANNULLOBJECT(disc);
CHKFORTRANNULLINTEGER(f);
*ierr = PetscDSGetFieldIndex(
	(PetscDS)PetscToPointer((prob) ),
	(PetscObject)PetscToPointer((disc) ),f);
}
PETSC_EXTERN void  petscdsgetfieldsize_(PetscDS prob,PetscInt *f,PetscInt *size, int *ierr)
{
CHKFORTRANNULLOBJECT(prob);
CHKFORTRANNULLINTEGER(size);
*ierr = PetscDSGetFieldSize(
	(PetscDS)PetscToPointer((prob) ),*f,size);
}
PETSC_EXTERN void  petscdsgetfieldoffset_(PetscDS prob,PetscInt *f,PetscInt *off, int *ierr)
{
CHKFORTRANNULLOBJECT(prob);
CHKFORTRANNULLINTEGER(off);
*ierr = PetscDSGetFieldOffset(
	(PetscDS)PetscToPointer((prob) ),*f,off);
}
PETSC_EXTERN void  petscdsgetfieldoffsetcohesive_(PetscDS ds,PetscInt *f,PetscInt *off, int *ierr)
{
CHKFORTRANNULLOBJECT(ds);
CHKFORTRANNULLINTEGER(off);
*ierr = PetscDSGetFieldOffsetCohesive(
	(PetscDS)PetscToPointer((ds) ),*f,off);
}
PETSC_EXTERN void  petscdsgetdimensions_(PetscDS prob,PetscInt *dimensions[], int *ierr)
{
CHKFORTRANNULLOBJECT(prob);
*ierr = PetscDSGetDimensions(
	(PetscDS)PetscToPointer((prob) ),dimensions);
}
PETSC_EXTERN void  petscdsgetcomponents_(PetscDS prob,PetscInt *components[], int *ierr)
{
CHKFORTRANNULLOBJECT(prob);
*ierr = PetscDSGetComponents(
	(PetscDS)PetscToPointer((prob) ),components);
}
PETSC_EXTERN void  petscdsgetcomponentoffset_(PetscDS prob,PetscInt *f,PetscInt *off, int *ierr)
{
CHKFORTRANNULLOBJECT(prob);
CHKFORTRANNULLINTEGER(off);
*ierr = PetscDSGetComponentOffset(
	(PetscDS)PetscToPointer((prob) ),*f,off);
}
PETSC_EXTERN void  petscdsgetcomponentoffsets_(PetscDS prob,PetscInt *offsets[], int *ierr)
{
CHKFORTRANNULLOBJECT(prob);
*ierr = PetscDSGetComponentOffsets(
	(PetscDS)PetscToPointer((prob) ),offsets);
}
PETSC_EXTERN void  petscdsgetcomponentderivativeoffsets_(PetscDS prob,PetscInt *offsets[], int *ierr)
{
CHKFORTRANNULLOBJECT(prob);
*ierr = PetscDSGetComponentDerivativeOffsets(
	(PetscDS)PetscToPointer((prob) ),offsets);
}
PETSC_EXTERN void  petscdsgetcomponentoffsetscohesive_(PetscDS ds,PetscInt *s,PetscInt *offsets[], int *ierr)
{
CHKFORTRANNULLOBJECT(ds);
*ierr = PetscDSGetComponentOffsetsCohesive(
	(PetscDS)PetscToPointer((ds) ),*s,offsets);
}
PETSC_EXTERN void  petscdsgetcomponentderivativeoffsetscohesive_(PetscDS ds,PetscInt *s,PetscInt *offsets[], int *ierr)
{
CHKFORTRANNULLOBJECT(ds);
*ierr = PetscDSGetComponentDerivativeOffsetsCohesive(
	(PetscDS)PetscToPointer((ds) ),*s,offsets);
}
PETSC_EXTERN void  petscdsgetnumboundary_(PetscDS ds,PetscInt *numBd, int *ierr)
{
CHKFORTRANNULLOBJECT(ds);
CHKFORTRANNULLINTEGER(numBd);
*ierr = PetscDSGetNumBoundary(
	(PetscDS)PetscToPointer((ds) ),numBd);
}
PETSC_EXTERN void  petscdsupdateboundarylabels_(PetscDS ds,DM dm, int *ierr)
{
CHKFORTRANNULLOBJECT(ds);
CHKFORTRANNULLOBJECT(dm);
*ierr = PetscDSUpdateBoundaryLabels(
	(PetscDS)PetscToPointer((ds) ),
	(DM)PetscToPointer((dm) ));
}
PETSC_EXTERN void  petscdscopyboundary_(PetscDS ds,PetscInt *numFields, PetscInt fields[],PetscDS newds, int *ierr)
{
CHKFORTRANNULLOBJECT(ds);
CHKFORTRANNULLINTEGER(fields);
CHKFORTRANNULLOBJECT(newds);
*ierr = PetscDSCopyBoundary(
	(PetscDS)PetscToPointer((ds) ),*numFields,fields,
	(PetscDS)PetscToPointer((newds) ));
}
PETSC_EXTERN void  petscdsdestroyboundary_(PetscDS ds, int *ierr)
{
CHKFORTRANNULLOBJECT(ds);
*ierr = PetscDSDestroyBoundary(
	(PetscDS)PetscToPointer((ds) ));
}
PETSC_EXTERN void  petscdsselectdiscretizations_(PetscDS prob,PetscInt *numFields, PetscInt fields[],PetscInt *minDegree,PetscInt *maxDegree,PetscDS newprob, int *ierr)
{
CHKFORTRANNULLOBJECT(prob);
CHKFORTRANNULLINTEGER(fields);
CHKFORTRANNULLOBJECT(newprob);
*ierr = PetscDSSelectDiscretizations(
	(PetscDS)PetscToPointer((prob) ),*numFields,fields,*minDegree,*maxDegree,
	(PetscDS)PetscToPointer((newprob) ));
}
PETSC_EXTERN void  petscdsselectequations_(PetscDS prob,PetscInt *numFields, PetscInt fields[],PetscDS newprob, int *ierr)
{
CHKFORTRANNULLOBJECT(prob);
CHKFORTRANNULLINTEGER(fields);
CHKFORTRANNULLOBJECT(newprob);
*ierr = PetscDSSelectEquations(
	(PetscDS)PetscToPointer((prob) ),*numFields,fields,
	(PetscDS)PetscToPointer((newprob) ));
}
PETSC_EXTERN void  petscdscopyequations_(PetscDS prob,PetscDS newprob, int *ierr)
{
CHKFORTRANNULLOBJECT(prob);
CHKFORTRANNULLOBJECT(newprob);
*ierr = PetscDSCopyEquations(
	(PetscDS)PetscToPointer((prob) ),
	(PetscDS)PetscToPointer((newprob) ));
}
PETSC_EXTERN void  petscdscopyconstants_(PetscDS prob,PetscDS newprob, int *ierr)
{
CHKFORTRANNULLOBJECT(prob);
CHKFORTRANNULLOBJECT(newprob);
*ierr = PetscDSCopyConstants(
	(PetscDS)PetscToPointer((prob) ),
	(PetscDS)PetscToPointer((newprob) ));
}
PETSC_EXTERN void  petscdscopyexactsolutions_(PetscDS ds,PetscDS newds, int *ierr)
{
CHKFORTRANNULLOBJECT(ds);
CHKFORTRANNULLOBJECT(newds);
*ierr = PetscDSCopyExactSolutions(
	(PetscDS)PetscToPointer((ds) ),
	(PetscDS)PetscToPointer((newds) ));
}
#if defined(__cplusplus)
}
#endif
