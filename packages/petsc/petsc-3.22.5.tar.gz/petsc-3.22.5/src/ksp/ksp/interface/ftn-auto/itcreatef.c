#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* itcreate.c */
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

#include "petscksp.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define kspload_ KSPLOAD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspload_ kspload
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define kspview_ KSPVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspview_ kspview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define kspviewfromoptions_ KSPVIEWFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspviewfromoptions_ kspviewfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define kspsetnormtype_ KSPSETNORMTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspsetnormtype_ kspsetnormtype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define kspsetchecknormiteration_ KSPSETCHECKNORMITERATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspsetchecknormiteration_ kspsetchecknormiteration
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define kspsetlagnorm_ KSPSETLAGNORM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspsetlagnorm_ kspsetlagnorm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define kspsetsupportednorm_ KSPSETSUPPORTEDNORM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspsetsupportednorm_ kspsetsupportednorm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define kspgetnormtype_ KSPGETNORMTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspgetnormtype_ kspgetnormtype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define kspsetoperators_ KSPSETOPERATORS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspsetoperators_ kspsetoperators
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define kspgetoperators_ KSPGETOPERATORS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspgetoperators_ kspgetoperators
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define kspgetoperatorsset_ KSPGETOPERATORSSET
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspgetoperatorsset_ kspgetoperatorsset
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define kspsetnestlevel_ KSPSETNESTLEVEL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspsetnestlevel_ kspsetnestlevel
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define kspgetnestlevel_ KSPGETNESTLEVEL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspgetnestlevel_ kspgetnestlevel
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define kspcreate_ KSPCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspcreate_ kspcreate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define kspsettype_ KSPSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspsettype_ kspsettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define kspgettype_ KSPGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define kspgettype_ kspgettype
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  kspload_(KSP newdm,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(newdm);
CHKFORTRANNULLOBJECT(viewer);
*ierr = KSPLoad(
	(KSP)PetscToPointer((newdm) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  kspview_(KSP ksp,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(ksp);
CHKFORTRANNULLOBJECT(viewer);
*ierr = KSPView(
	(KSP)PetscToPointer((ksp) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  kspviewfromoptions_(KSP A,PetscObject obj, char name[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(obj);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = KSPViewFromOptions(
	(KSP)PetscToPointer((A) ),
	(PetscObject)PetscToPointer((obj) ),_cltmp0);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  kspsetnormtype_(KSP ksp,KSPNormType *normtype, int *ierr)
{
CHKFORTRANNULLOBJECT(ksp);
*ierr = KSPSetNormType(
	(KSP)PetscToPointer((ksp) ),*normtype);
}
PETSC_EXTERN void  kspsetchecknormiteration_(KSP ksp,PetscInt *it, int *ierr)
{
CHKFORTRANNULLOBJECT(ksp);
*ierr = KSPSetCheckNormIteration(
	(KSP)PetscToPointer((ksp) ),*it);
}
PETSC_EXTERN void  kspsetlagnorm_(KSP ksp,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(ksp);
*ierr = KSPSetLagNorm(
	(KSP)PetscToPointer((ksp) ),*flg);
}
PETSC_EXTERN void  kspsetsupportednorm_(KSP ksp,KSPNormType *normtype,PCSide *pcside,PetscInt *priority, int *ierr)
{
CHKFORTRANNULLOBJECT(ksp);
*ierr = KSPSetSupportedNorm(
	(KSP)PetscToPointer((ksp) ),*normtype,*pcside,*priority);
}
PETSC_EXTERN void  kspgetnormtype_(KSP ksp,KSPNormType *normtype, int *ierr)
{
CHKFORTRANNULLOBJECT(ksp);
*ierr = KSPGetNormType(
	(KSP)PetscToPointer((ksp) ),normtype);
}
PETSC_EXTERN void  kspsetoperators_(KSP ksp,Mat Amat,Mat Pmat, int *ierr)
{
CHKFORTRANNULLOBJECT(ksp);
CHKFORTRANNULLOBJECT(Amat);
CHKFORTRANNULLOBJECT(Pmat);
*ierr = KSPSetOperators(
	(KSP)PetscToPointer((ksp) ),
	(Mat)PetscToPointer((Amat) ),
	(Mat)PetscToPointer((Pmat) ));
}
PETSC_EXTERN void  kspgetoperators_(KSP ksp,Mat *Amat,Mat *Pmat, int *ierr)
{
CHKFORTRANNULLOBJECT(ksp);
PetscBool Amat_null = !*(void**) Amat ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(Amat);
PetscBool Pmat_null = !*(void**) Pmat ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(Pmat);
*ierr = KSPGetOperators(
	(KSP)PetscToPointer((ksp) ),Amat,Pmat);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! Amat_null && !*(void**) Amat) * (void **) Amat = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! Pmat_null && !*(void**) Pmat) * (void **) Pmat = (void *)-2;
}
PETSC_EXTERN void  kspgetoperatorsset_(KSP ksp,PetscBool *mat,PetscBool *pmat, int *ierr)
{
CHKFORTRANNULLOBJECT(ksp);
*ierr = KSPGetOperatorsSet(
	(KSP)PetscToPointer((ksp) ),mat,pmat);
}
PETSC_EXTERN void  kspsetnestlevel_(KSP ksp,PetscInt *level, int *ierr)
{
CHKFORTRANNULLOBJECT(ksp);
*ierr = KSPSetNestLevel(
	(KSP)PetscToPointer((ksp) ),*level);
}
PETSC_EXTERN void  kspgetnestlevel_(KSP ksp,PetscInt *level, int *ierr)
{
CHKFORTRANNULLOBJECT(ksp);
CHKFORTRANNULLINTEGER(level);
*ierr = KSPGetNestLevel(
	(KSP)PetscToPointer((ksp) ),level);
}
PETSC_EXTERN void  kspcreate_(MPI_Fint * comm,KSP *inksp, int *ierr)
{
PETSC_FORTRAN_OBJECT_CREATE(inksp);
 PetscBool inksp_null = !*(void**) inksp ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(inksp);
*ierr = KSPCreate(
	MPI_Comm_f2c(*(comm)),inksp);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! inksp_null && !*(void**) inksp) * (void **) inksp = (void *)-2;
}
PETSC_EXTERN void  kspsettype_(KSP ksp,char *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(ksp);
/* insert Fortran-to-C conversion for type */
  FIXCHAR(type,cl0,_cltmp0);
*ierr = KSPSetType(
	(KSP)PetscToPointer((ksp) ),_cltmp0);
  FREECHAR(type,_cltmp0);
}
PETSC_EXTERN void  kspgettype_(KSP ksp,char *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(ksp);
*ierr = KSPGetType(
	(KSP)PetscToPointer((ksp) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for type */
*ierr = PetscStrncpy(type, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, type, cl0);
}
#if defined(__cplusplus)
}
#endif
